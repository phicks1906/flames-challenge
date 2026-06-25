import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
 "Access-Control-Allow-Origin": "*",
 "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-fc-secret",
};

serve(async (req) => {
 if (req.method === "OPTIONS") {
   return new Response("ok", { headers: corsHeaders });
 }

 const secret = req.headers.get("x-fc-secret");
 if (secret !== Deno.env.get("FC_FN_SECRET")?.trim()) {
   return new Response(JSON.stringify({ error: "Unauthorized" }), {
     status: 401,
     headers: { ...corsHeaders, "Content-Type": "application/json" },
   });
 }

 const body = await req.json();
 const { type, userIds, category, month, deadline } = body;

 if (!userIds || !userIds.length) {
   return new Response(JSON.stringify({ error: "No userIds" }), {
     status: 400,
     headers: { ...corsHeaders, "Content-Type": "application/json" },
   });
 }

 const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY")?.trim();
 const RESEND_FROM = Deno.env.get("RESEND_FROM")?.trim();

 const supabase = createClient(
   Deno.env.get("SUPABASE_URL")!,
   Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
 );

 const subjects: Record<string, string> = {
   won: `🏆 You're the ${category} Champion!`,
   qualified: `⚡ You qualified for the ${category} Championship`,
   sudden_death: `⚡ Sudden Death — ${category} Championship is tied!`,
 };

 const bodies: Record<string, string> = {
   won: `Congratulations! You won the ${category} Championship${month ? " for " + month : ""}. Your title is now recorded in the Hall of Fame. 🏆`,
   qualified: `You've qualified for the ${category} Championship Challenge! Submit your entry${deadline ? " by " + deadline : ""} to compete for the title.`,
   sudden_death: `The ${category} Championship is tied! Voting has reset — cast your vote again to crown the champion.`,
 };

 const subject = subjects[type] || `FlamesChallenge — ${category} Update`;
 const text = bodies[type] || `You have a new update in the ${category} Championship.`;

 const results = [];
 for (const userId of userIds) {
   const { data: authUser } = await supabase.auth.admin.getUserById(userId);
   const email = authUser?.
